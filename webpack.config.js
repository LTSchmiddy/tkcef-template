const path = require('path');
const webpack = require("webpack");

// __webpack_base_uri__ = 'http://localhost:8080';
const HtmlWebpackPlugin = require('html-webpack-plugin');


// Define Webpack Config:
module.exports = (env, options) => {

    let wpMode = "development";
    if (options.mode != undefined) {
        wpMode = options.mode;
    }

    let wpDest = "./dist/webpack/" + wpMode;

    console.log(`Webpack Mode: '${wpMode}'`);

    return {
        mode: wpMode,
        entry: path.resolve(__dirname, 'src/webpack/main.ts'),
        output: {
            publicPath: "",
            path: path.resolve(__dirname, wpDest),
            filename: 'app.bundle.js',
            libraryTarget: 'var',
            library: 'app'
        },
        module: {
            rules: [
                {
                    test: /\.json$/,
                    loader: 'json5-loader',
                    type: 'javascript/auto'
                },
                {
                    test: /\.tsx?$/,
                    use: 'ts-loader',
                    exclude: /node_modules/,
                },
                // {
                //     test: /\.jsx?$/,
                //     use: 'js-loader',
                //     exclude: /node_modules/,
                // },
                {
                    test: /\.html$/,
                    loader: 'html-loader',
                    exclude: /index.html/
                },
                {
                    test: /\.htm$/,
                    use: [
                        'html-loader'
                    ],
                },
                {
                    test: /\.css$/,
                    use: [
                        'style-loader',
                        'css-loader',
                    ],
                },
                {
                    test: /(?<!\.m)\.s[ac]ss$/i,
                    use: [
                        {
                        // inject CSS to page
                            loader: 'style-loader'
                        }, {
                        // translates CSS into CommonJS modules
                            loader: 'css-loader'
                        }, {
                        // Run postcss actions
                            loader: 'postcss-loader',
                            options: {
                                // `postcssOptions` is needed for postcss 8.x;
                                // if you use postcss 7.x skip the key
                                postcssOptions: {
                                // postcss plugins, can be exported to postcss.config.js
                                    plugins: function () {
                                        return [
                                            require('autoprefixer')
                                        ];
                                    }
                                }
                            }
                        }, {
                        // compiles Sass to CSS
                            loader: 'sass-loader'
                        }
                    ],
                },
                {
                    test: /\.m\.s[ac]ss$/i,
                    use: [
                        'css-loader',
                        'sass-loader',
                    ],
                },
                {
                    test: /\.(png|svg|jpg|gif)$/,
                    use: [
                        'file-loader',
                    ],
                },
            ],
        },
        node: {
            global: true
        },
        resolve: {
            alias: {
                src_webpack: path.resolve(__dirname, "src/webpack/"),
            },
            extensions: [
                '.tsx',
                '.ts',
                '.jsx',
                '.js',
                '.json'
            ],
        },
        plugins: [
            new webpack.ProvidePlugin({
            // jQuery:
            $: 'jquery',
            jQuery: 'jquery',
            "window.$": 'jquery',
            "window.jQuery": 'jquery',

            // Lodash:
            _: 'lodash',
            lodash: 'lodash',
            "window._": 'lodash',
            "window.lodash": 'lodash',
            }),
            new HtmlWebpackPlugin({
                filename: 'index.html',
                template: 'src/pages/index.html',
                scriptLoading: 'blocking'
            }),
        ]
    };
};

console.log("Webpack Config Loaded...");