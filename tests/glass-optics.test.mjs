import test from 'node:test';
import assert from 'node:assert/strict';
import {lensOffset} from '../assets/js/components/liquid-glass.js';

test('the lens sampling map stays continuous and never folds at edges or corners', () => {
  for (const [width, height] of [[320, 82], [864, 62], [1156, 62]]) {
    const sample = (x, y) => {
      const [dx, dy] = lensOffset(x, y, width, height);
      assert.ok(Math.hypot(dx, dy) <= 2, 'displacement must remain below two pixels');
      return [x + dx, y + dy];
    };
    // Finite differences check the actual 2D sampling map, including the
    // transition from straight sides to rounded corners and the flat centre.
    const epsilon = .05;
    for (let distanceX = -.5; distanceX <= 36; distanceX += .5) {
      for (let distanceY = -.5; distanceY <= 36; distanceY += .5) {
        for (const [x, y] of [[distanceX, distanceY], [width - distanceX, height - distanceY], [width / 2, distanceY]]) {
          const xp = sample(x + epsilon, y), xm = sample(x - epsilon, y);
          const yp = sample(x, y + epsilon), ym = sample(x, y - epsilon);
          const a = (xp[0] - xm[0]) / (2 * epsilon), b = (yp[0] - ym[0]) / (2 * epsilon);
          const c = (xp[1] - xm[1]) / (2 * epsilon), d = (yp[1] - ym[1]) / (2 * epsilon);
          assert.ok(a > .59 && d > .59 && a * d - b * c > .35, `fold at ${width}x${height}: ${x},${y}`);
        }
      }
    }
    assert.deepEqual(lensOffset(width / 2, height / 2, width, height), [0, 0]);
    assert.deepEqual(lensOffset(-10, height / 2, width, height), [0, 0]);
  }
});
