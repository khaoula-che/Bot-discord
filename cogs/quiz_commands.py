import discord
from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime, timedelta
import json
import asyncio

USER_DATA_FILE = 'user_data.json'  # Define the path for user data

class QuizCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_reminder.start()  # Start the reminder task
        self.quizzes = self.load_quizzes()
        self.participants = []
        self.user_data = self.load_user_data()  # Load user data at start
        self.current_quiz_title = ""
        self.current_quiz_date = ""
        self.quiz_active = False  # Flag to check if a quiz is active

    def load_quizzes(self):
        with open('quizzes.json', 'r') as f:
            return json.load(f)

    def load_user_data(self):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)

    def save_user_data(self):
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(self.user_data, f, indent=4)

    @tasks.loop(seconds=5)  # Check every 5 seconds for testing
    async def send_reminder(self):
        now = datetime.now()
        print(f"Démarrage de la vérification des quiz à {now}")  # Debug print
        for quiz in self.quizzes:
            quiz_time = f"{quiz['date']} {quiz['time']}"
            quiz_datetime = datetime.strptime(quiz_time, "%Y-%m-%d %H:%M")

            # Only send participation request at the exact time of the quiz
            if now >= quiz_datetime and now < quiz_datetime + timedelta(seconds=5):  # A 5 second window
                channel = get(self.bot.get_all_channels(), name="quiz-hebdomadaires")
                if channel:
                    print(f"Envoi d'un message de participation dans le canal: {channel.name}")  # Debug print
                    await self.ask_participation(channel, quiz)
                else:
                    print("Canal 'quiz-hebdomadaires' non trouvé.")  # Debug print

    async def ask_participation(self, channel, quiz):
        if self.quiz_active:  # Check if a quiz is already active
            return

        view = discord.ui.View()
        participate_button = discord.ui.Button(label="Participer", style=discord.ButtonStyle.primary)
        participate_button.callback = self.participate_callback
        view.add_item(participate_button)

        await channel.send(f"@everyone Le quiz '{quiz['name']}' commence maintenant! Voulez-vous participer?", view=view)

        self.participants = []
        self.quiz_active = True  # Set the quiz as active

        await asyncio.sleep(60)  # Wait for 1 minute for participants to join

        if self.participants:
            await self.start_quiz(channel, quiz)
        else:
            self.quiz_active = False  # Reset the active flag
            await channel.send("Personne n'a rejoint le quiz. Annulation. 😢")

    async def participate_callback(self, interaction: discord.Interaction):
        participant_user = interaction.user
        if participant_user not in [p['user'] for p in self.participants]:
            # Add participant but give them participation point
            self.participants.append({'user': participant_user, 'score': 0})  # Start with 0 points
            # Increment participation points
            self.update_participation_points(participant_user)
            await interaction.response.send_message("Merci pour votre participation! Le quiz va commencer bientôt.", ephemeral=True)
        else:
            await interaction.response.send_message("Vous êtes déjà inscrit pour ce quiz.", ephemeral=True)

    def update_participation_points(self, participant_user):
        for user_data in self.user_data:
            if user_data['username'] == participant_user.name:
                user_data['points'] += 1  # Add participation point
                break  # Exit the loop once user is found
        self.save_user_data()  # Save updated user data

    async def start_quiz(self, channel, quiz):
        self.current_quiz_title = quiz['name']
        self.current_quiz_date = quiz['date']

        for question in quiz['questions']:
            await self.ask_question(channel, question)

        await self.show_results(channel)
        self.quiz_active = False  # Reset the active flag after the quiz is finished

    async def ask_question(self, channel, question):
        options = question['options']
        correct_answer = question['correct_answer']

        view = discord.ui.View()
        for option in options:
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary)
            button.callback = self.answer_callback
            button.custom_id = f"answer_{option}"  # Use custom_id to identify the button
            view.add_item(button)

        question_msg = await channel.send(f"**{question['question']}**", view=view)

        # Wait for responses
        responses = {}  # Dictionary to store participant responses

        def check(interaction):
            return interaction.message.id == question_msg.id

        for p in self.participants:
            try:
                interaction = await self.bot.wait_for("interaction", timeout=30.0, check=check)
                answer = interaction.data['custom_id'].split('_')[1]
                participant = interaction.user

                responses[participant] = answer  # Store the response

                if answer == correct_answer:
                    await interaction.response.send_message(f"{participant.display_name}, bonne réponse! 🎉", ephemeral=True)
                    p['score'] += 1  # Increment score for correct answer
                else:
                    await interaction.response.send_message(f"{participant.display_name}, mauvaise réponse. La bonne réponse était **{correct_answer}**.", ephemeral=True)

            except asyncio.TimeoutError:
                await channel.send(f"{p['user'].display_name} n'a pas répondu à temps. Question ignorée.")

        # Disable buttons after all responses are collected
        for item in view.children:
            item.disabled = True
        await question_msg.edit(view=view)

    async def answer_callback(self, interaction: discord.Interaction):
        pass  # Placeholder callback for answer buttons

    async def show_results(self, channel):
        # Sort participants by score
        sorted_participants = sorted(self.participants, key=lambda x: x['score'], reverse=True)

        # Prepare the leaderboard message
        leaderboard_message = f"**🏆 Résultats du quiz '{self.current_quiz_title}' du {self.current_quiz_date} :**\n"
        leaderboard_message += "Voici le classement final :\n\n"

        # Display all participants
        for i, p in enumerate(sorted_participants):
            leaderboard_message += f"{i + 1}. **{p['user'].display_name}**: {p['score']} point(s)\n"

        # Send leaderboard to channel
        await channel.send(leaderboard_message)

        # Send the leaderboard to the "admin-organisation" channel
        admin_channel = get(self.bot.get_all_channels(), name="admin-organisation")
        if admin_channel:
            await admin_channel.send(leaderboard_message)  # Send the leaderboard to admin channel
        else:
            print("Canal 'admin-organisation' non trouvé.")  # Debug print

        # Update user data with scores
        for p in sorted_participants:
            user_name = p['user'].name
            user_score = p['score']
            # Find user in user_data
            for user_data in self.user_data:
                if user_data['username'] == user_name:
                    user_data['points'] += user_score  # Update the user's score
                    break  # Exit the loop once user is found

        self.save_user_data()  # Save updated user data

        # Send individual results to participants not in top 3
        for i, p in enumerate(sorted_participants):
            if i >= 3:  # Not in top 3
                personalized_message = f"**Classement :** Vous êtes {i + 1} avec {p['score']} point(s)."

                # Add personalized messages based on ranking
                if p['score'] == 0:
                    personalized_message += "\nMalheureusement, vous n'avez pas réussi à marquer. Essayez de nouveau!"
                elif p['score'] == 1:
                    personalized_message += "\nUn bon début! Continuez à vous améliorer!"
                elif p['score'] == 2:
                    personalized_message += "\nPresque dans le top 3! Plus de pratique vous aidera!"
                else:
                    personalized_message += "\nVous avez bien joué, mais le podium vous attend la prochaine fois!"

                await p['user'].send(personalized_message)  # Send a DM to the participant

    @send_reminder.before_loop
    async def before_send_reminder(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(QuizCommands(bot))
