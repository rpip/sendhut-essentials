// https://github.com/mozilla/bedrock/blob/79850bae56d320ed89934028e085db9beba360ea/gulpfile.js
// https://stackoverflow.com/questions/26085364/is-it-possible-to-configure-gulp-livereload-for-django
// https://stackoverflow.com/a/37901414
import gulp from 'gulp';
import autoprefixer from 'autoprefixer';
import browserify from 'browserify';
import watchify from 'watchify';
import source from 'vinyl-source-stream';
import buffer from 'vinyl-buffer';
import eslint from 'gulp-eslint';
import babelify from 'babelify';
import uglify from 'gulp-uglify';
import rimraf from 'rimraf';
import notify from 'gulp-notify';
import browserSync, { reload } from 'browser-sync';
import sourcemaps from 'gulp-sourcemaps';
import postcss from 'gulp-postcss';
import rename from 'gulp-rename';
import nested from 'postcss-nested';
import vars from 'postcss-simple-vars';
import extend from 'postcss-simple-extend';
import cssnano from 'cssnano';
import htmlReplace from 'gulp-html-replace';
import imagemin from 'gulp-imagemin';
import pngquant from 'imagemin-pngquant';
import runSequence from 'run-sequence';
import sass from 'gulp-sass';
import size from 'gulp-size';
import concat from 'gulp-concat';
import minify from 'gulp-minify';

var spawn = require('child_process').spawn;

const paths = {
  bundle: 'app.js',
  srcCss: 'styles/**/**/*.scss',
  srcImg: 'images/**',
  srcLint: ['js/*.js'],
  dist: 'dist',
  distCss: 'dist/css',
  distJs: 'dist/js',
  distImg: 'dist/images'
};


gulp.task('clean', cb => {
  rimraf('dist', cb);
});


// copy web fonts to dist
gulp.task('fonts', function() {
  return gulp.src(['fonts/**'])
    .pipe(gulp.dest('dist/fonts'))
    .pipe(size({
      title: 'fonts'
    }));
});

// sass
gulp.task('sass', () => {
  gulp.src(paths.srcCss)
    .pipe(rename({
      extname: '.css'
    }))
    .pipe(sass({
      outputStyle: 'compressed'
    }).on('error', sass.logError))
    .pipe(gulp.dest(paths.distCss))
    .pipe(reload({
      stream: true
    }));
});

gulp.task('images', () => {
  gulp.src(paths.srcImg)
    .pipe(imagemin({
      progressive: true,
      svgoPlugins: [{
        removeViewBox: false
      }],
      use: [pngquant()]
    }))
    .pipe(gulp.dest(paths.distImg));
});

// copy vendor files from /node_modules
// note: requires `npm install` before running!
gulp.task('vendor', function() {
  gulp.src(['node_modules/sass-rem/_rem.scss'])
    .pipe(gulp.dest('styles'))

  gulp.src(['node_modules/bootstrap/scss/**/*'])
    .pipe(gulp.dest('styles/bootstrap'))

  gulp.src([
    'node_modules/jquery/dist/jquery.js',
    'node_modules/popper.js/dist/umd/popper.js',
    'node_modules/bootstrap/dist/js/bootstrap.js',
    'node_modules/scrollpos-styler/scrollPosStyler.js',
    'node_modules/holderjs/holder.js',
    'node_modules/js-cookie/src/js.cookie.js',
    'node_modules/form-serializer/dist/jquery.serialize-object.min.js'
  ]).pipe(gulp.dest('dist/vendor'))

  gulp.src(['node_modules/source-sans-pro/**/*'])
    .pipe(gulp.dest('fonts/source-sans-pro'))

  gulp.src(['vendor/slidepanel/**/*'])
    .pipe(gulp.dest('dist/vendor/slidepanel'))

  gulp.src(['vendor/clipboard.min.js'])
    .pipe(gulp.dest('dist/vendor'))
});

gulp.task('watchTask', () => {
  gulp.watch('styles/main.scss', ['sass', 'images']);
//gulp.watch('js/app.js', ['js-build']);
});

gulp.task('lint', () => {
  gulp.src(paths.srcLint)
    .pipe(eslint())
    .pipe(eslint.format())
    .pipe(gulp.dest(paths.distJs));
});


gulp.task('build', cb => {
  process.env.NODE_ENV = 'production';
  runSequence('clean', ['vendor', 'fonts', 'images', 'lint', 'sass'], cb);
});

gulp.task('browserSync', function() {
  browserSync.init({
    notify: false,
    proxy: "localhost:8000"
  });
});

gulp.task('default', ['build', 'watchTask']);
