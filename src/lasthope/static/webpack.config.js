// https://webpack.js.org/guides/author-libraries/
const config = {
    entry: ['./index.js'],
    output: {
        path: __dirname + '/build',
        filename: 'helpers.js',
        library: 'helpers',
        libraryTarget:'var',
    },
    module: {
        loaders: [
            {
                loader:'babel-loader',
                test: /\.js$/,
                exclude:  /node_modules/,
                query: {
                    presets: ['es2015', 'react']
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js']
    },
    devServer:{
        port: 3000,
        contentBase: __dirname + '/build',
        inline: true
    }
}
module.exports = config;
