# Use at your own risk

## In plain words

- **This project is free and comes with no promise.** Nobody promises that it works, that it is correct, or that it is safe for your instance.
- **A model can write a wrong flow.** A wrong flow can change or delete records, send email, call other systems or stop a business process. Read every flow before you turn it on. What is in the imported file is what runs.
- **Test somewhere safe first.** Use an instance that is not production. Know how to back out the update set before you commit it.
- **It uses parts of ServiceNow that are not documented.** The update-set format for flows and the activation call are not public interfaces. ServiceNow can change them at any time, and a rule that worked on one release can fail on the next.
- **You must follow your own agreements.** Check that your use fits your contract with ServiceNow and the rules of your own organisation. This project gives no legal or professional advice.
- **Be careful what you give a model.** Do not paste scripts, data or records from your employer or a customer into a model unless you are allowed to.
- **The activation call needs an administrator.** It runs with the rights of the person who sends it. A flow can also run as the system user, with more rights than the person who started it.
- **There is no support.** The author has no duty to answer questions, fix problems or keep anything up to date.
- **You are responsible for the result.** You choose to use this project. What happens on your instance is your responsibility, not the author's.
- **You cover the author's costs.** If your use of this project leads to a claim against the author, you agree to pay the author's costs, as far as the law allows.
- **A model helped to write it.** Large parts of the prompt, the tools and these documents were written with an AI model. They were tested, but they can still be wrong.
- **This is a personal project.** It is not a product of the author's employer and does not speak for them. It is not affiliated with ServiceNow.

## The formal version

THE PROMPT, CODE, DOCUMENTATION AND ALL OTHER MATERIALS IN THIS REPOSITORY, AND ANY OUTPUT PRODUCED WITH THEM, ARE PROVIDED "AS IS" AND "AS AVAILABLE", WITHOUT WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR STATUTORY, INCLUDING WITHOUT LIMITATION ANY WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY, TITLE OR NON-INFRINGEMENT.

TO THE MAXIMUM EXTENT PERMITTED BY LAW, IN NO EVENT WILL THE AUTHOR OR ANY CONTRIBUTOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, CONSEQUENTIAL OR PUNITIVE DAMAGES, OR FOR ANY LOSS OF DATA, PROFITS, BUSINESS OR SERVICE, ARISING FROM OR RELATED TO THE MATERIALS OR THEIR OUTPUT, HOWEVER CAUSED AND UNDER ANY THEORY OF LIABILITY, EVEN IF ADVISED THAT SUCH DAMAGE WAS POSSIBLE. YOU USE THE MATERIALS AND ANY OUTPUT AT YOUR SOLE RISK.

To the extent permitted by law, you agree to indemnify, defend and hold harmless the author and contributors from any claim, damage, loss or cost, including reasonable legal fees, that arises from your use of the materials or their output, from your breach of any agreement with a third party, including ServiceNow, or from your violation of any law.

THE AUTHOR HAS NO OBLIGATION TO PROVIDE SUPPORT, MAINTENANCE, UPDATES OR CORRECTIONS. THE MATERIALS ARE A PERSONAL PROJECT AND ARE NOT A PRODUCT OF, AND DO NOT REPRESENT, THE AUTHOR'S EMPLOYER OR SERVICENOW. YOU ARE SOLELY RESPONSIBLE FOR COMPLYING WITH YOUR OWN AGREEMENTS, INCLUDING ANY AGREEMENT WITH SERVICENOW, AND WITH THE POLICIES OF YOUR ORGANISATION.

Nothing in this notice limits a liability that the law does not allow to be limited. The licences in this repository carry their own disclaimers, which also apply. This notice is not a condition of either licence. It does not limit or take away any right that those licences give you, and you do not have to pass it on with copies you share.
