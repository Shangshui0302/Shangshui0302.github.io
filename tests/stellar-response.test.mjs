import test from 'node:test';
import assert from 'node:assert/strict';
import {createStellarResponse} from '../assets/js/scenes/stellar-response.js';

test('charged star releases continuously, overshoots, then settles at 30 and 60 fps', () => {
  for (const fps of [30, 60]) {
    const response = createStellarResponse();
    for (let i = 0; i < fps * 2; i++) response.step(Math.min(i / (fps * 1.65), 1), 1 / fps);
    const compressed = response.displacement;
    assert.ok(compressed < -.25);
    response.step(0, 1 / fps);
    assert.ok(Math.abs(response.displacement - compressed) < .02, 'first release frame must retain compression');
    let peak = 0, trough = 0;
    for (let i = 1; i < fps * 2; i++) {
      response.step(0, 1 / fps);
      peak = Math.max(peak, response.displacement);
      if (peak > 0) trough = Math.min(trough, response.displacement);
    }
    assert.ok(peak > .07 && peak < .12, 'visible outward rebound');
    assert.ok(trough < -.015, 'one smaller inward rebound');
    assert.ok(Math.abs(response.displacement) < .001 && Math.abs(response.velocity) < .006);
  }
});

test('recharging preserves momentum and explicit reset clears all response', () => {
  const response = createStellarResponse();
  for (let i = 0; i < 120; i++) response.step(1, 1 / 60);
  for (let i = 0; i < 12; i++) response.step(0, 1 / 60);
  const before = {...response};
  response.step(.01, .00001);
  assert.ok(Math.abs(response.displacement - before.displacement) < .0001);
  assert.ok(Math.abs(response.velocity - before.velocity) < .001);
  response.reset();
  assert.equal(response.displacement, 0);
  assert.equal(response.velocity, 0);
  assert.equal(response.heat, 0);
});
