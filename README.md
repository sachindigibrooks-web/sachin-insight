# sachin-insight

## Osho sketch (p5.brush demo)

`osho-sketch/` is an animated pencil-and-ink portrait drawn live with
[p5.brush](https://github.com/acamposuribe/p5.brush). Each portrait is built up in layers
(charcoal block-in, tonal hatching, cross-hatching, eraser highlights, fine detail, ink accents),
following contours detected in a reference photo; when one finishes it rests, then the next begins.
Click the canvas to skip ahead.

```sh
npm install
npm start          # then open http://localhost:8080/osho-sketch/
```

Tune passes, stroke counts and per-photo crop/vignette/gamma at the top of `osho-sketch/sketch.js`.

Photos (Wikimedia Commons):
- `images/osho-2.jpg`: [Jayendra Lashkari](https://commons.wikimedia.org/wiki/File:Osho_Rajneesh_2.jpg), CC BY-SA 3.0
- `images/osho-1.jpg`: [Marcel Antonisse / Anefo, Nationaal Archief](https://commons.wikimedia.org/wiki/File:Osho_Rajneesh.jpg), CC0
