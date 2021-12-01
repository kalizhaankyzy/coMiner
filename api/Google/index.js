const root = document.querySelector('#result')
const btn = document.querySelector('#find')
const input= document.querySelector('#input')
const API_KEY = 'AIzaSyAUHBeU9Rzj3Iw7AVSDFOWSPAc4rGFZlts&cx=eef1ce54ee2a2ef00&'
const API_KEY_2='AIzaSyC6ew8yX8jbVDhD6zzZ-Bs6lUwR05D5l5s&cx=aaab32314809a8355&' // kbtu
const API_KEY_3='AIzaSyAUHBeU9Rzj3Iw7AVSDFOWSPAc4rGFZlts&cx=c23c8927750a7737f&'



const patternMaker = (EN) => {
    return [
        `vs ${EN}`,
        `${EN} vs`,
        `${EN} or`,
        `or ${EN}`,
        `such as ${EN} * or OR and`,
        `especially ${EN},`,
        `including ${EN},`,
    ]
}

const getResults = (queryString) => {
    const promises = [];

    for(let i = 1; i <=91 ; i+=10){
        promises.push(fetch(`https://www.googleapis.com/customsearch/v1?key=${API_KEY_2}q="${queryString}"&start=${i}&safe=active`))
    }
    return promises
}


const work = () => {
    const patterns = patternMaker('Facebook')

    for(let i = 0 ;i < patterns.length; i++) {
       setTimeout(() => {
            const promises = getResults(patterns[i])
            Promise.all(promises)
                .then(results => Promise.all(results.map(r => r.json())))
                .then((a) => {
                    const b = {}
                    for (let i = 0; i < a.length; i++) {
                        b[`${i + 1}`] = a[i]
                    }
                    console.debug('results for',(patterns[i])
                    console.log(JSON.stringify(b))
                })
           }, 5000*i)
    }
}

const handleGetCompetitorList = () => {
    const promises = getResults(patterns[6])
    Promise.all(promises)
        .then(results => Promise.all(results.map(r => r.json())))
        .then((a) => {
            const b = {}
            for (let i = 0; i < a.length; i++) {
                b[`${i + 1}`] = a[i]
            }
            console.log(JSON.stringify(b))
        })
}




btn.addEventListener('click', work )
