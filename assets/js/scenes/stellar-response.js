/* Keep visual deformation independent of the held input. The underdamped
   spring retains position and velocity when its target changes on release. */
export function createStellarResponse() {
  const frequency = 11, damping = 3.4;
  const oscillation = Math.sqrt(frequency ** 2 - damping ** 2);
  return {
    displacement: 0, velocity: 0, heat: 0,
    step(charge, dt) {
      const target = -.27 * charge;
      const offset = this.displacement - target;
      const c = (this.velocity + damping * offset) / oscillation;
      const decay = Math.exp(-damping * dt);
      const cos = Math.cos(oscillation * dt), sin = Math.sin(oscillation * dt);
      // Exact solution for this frame's target; stable at mobile frame rates.
      this.displacement = target + decay * (offset * cos + c * sin);
      this.velocity = decay * (this.velocity * cos - (damping * c + oscillation * offset) * sin);
      this.heat += (charge - this.heat) * (1 - Math.exp(-dt * 6));
    },
    reset() { this.displacement = this.velocity = this.heat = 0; },
  };
}
