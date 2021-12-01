// Used thus api to search query for step 2.

const entity_name = 'Python'
const competitors_list = ['R', 'Java', 'Javascript', 'C', 'Ruby', 'Matlab', 'Php', 'Gatoroid', 'Go', 'Golang']

// const entity_name = 'Toyota'
// const competitors_list = ['Honda', 'Nissan', 'Competition', 'Chevrolet', 'Subaru', 'Lexus', 'Ford', 'Volkswagen', 'Kia', 'Tesla']

// const entity_name = 'Prada'
// const competitors_list  = ['Gucci', 'Louis vuitton', 'Fendi', 'Miu miu', 'Chanel', 'Versace', 'Rajput', 'Nada', 'Azam', 'Chloe']

// const entity_name = 'Adidas'
// const competitors_list = ['Nike', 'Puma', 'Pace', 'Advantage', 'Footjoy', 'Legacy lifter', 'Converse', 'Reebok', 'Position', 'Everybody']

// const entity_name = 'Twix'
// const competitors_list = ['Right', 'Snickers', 'Kit Kat', 'Left', 'Mars', 'Treat', 'Reese', 'Aldi', 'Carmel', 'Donut']

// const entity_name = 'Facebook'
// const competitors_list = ['Instagram', 'Twitter', 'Google', 'Apple', 'Youtube', 'Linkedin', 'Snapchat', 'Twitch', 'Australia', 'Whatsapp']

// const entity_name = 'Amazon'
// const competitors_list= ['Walmart', 'Google', 'Apple', 'Shopify', 'Microsoft', 'Alibaba', 'Netflix', 'Prime', 'Hachette', 'Youtube']


document.querySelector('button').addEventListener('click',() => {

for(let i = 0 ; i < competitors_list.length; i++){
    setTimeout(() => {
        fetch(`https://google-search3.p.rapidapi.com/api/v1/search/q="${entity_name} ${competitors_list[i]}"&num=100`, {
        "method": "GET",
        "headers": {
            "x-user-agent": "desktop",
            "x-proxy-location": "US",
            "x-rapidapi-host": "google-search3.p.rapidapi.com",
            "x-rapidapi-key": "7f8125dcb0msh08515a300803345p1fc8ecjsn17b9538f872f"
        }
    })
    .then(response => {
        return response.json()
    })
    .then(res => {
        console.log(JSON.stringify(res))})
    .catch(err => {
        console.error(err);
    });
    }, i *1000)}
})