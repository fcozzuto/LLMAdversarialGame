def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Legal moves (engine keeps you in place if invalid, but we avoid that)
    best = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            if resources:
                # Evaluate this move by how much it improves our standing on resources.
                # lead = opp_dist - our_dist (positive => we are closer)
                best_lead = -10**9
                worst_lead = 10**9
                for rx, ry in resources:
                    sd = man(nx, ny, rx, ry)
                    od = man(ox, oy, rx, ry)
                    lead = od - sd
                    if lead > best_lead:
                        best_lead = lead
                    if lead < worst_lead:
                        worst_lead = lead

                # If we're behind everywhere, focus on the most "swingable" resource (worst_lead)
                # by maximizing our improvement relative to being behind.
                if best_lead <= 0:
                    target_improve = -10**9
                    for rx, ry in resources:
                        sd0 = man(sx, sy, rx, ry)
                        od = man(ox, oy, rx, ry)
                        lead0 = od - sd0
                        sd1 = man(nx, ny, rx, ry)
                        lead1 = od - sd1
                        improve = lead1 - lead0
                        if improve > target_improve:
                            target_improve = improve
                    lead_term = target_improve * 6.0
                else:
                    # Otherwise commit to the resource where we're (becoming) closest.
                    lead_term = best_lead * 5.0

                # Denial pressure: if opponent is close, avoid helping their current approach too much.
                # Encourage some distance when we're not clearly winning a resource race.
                d_op = man(nx, ny, ox, oy)
                dist_term = (d_op - man(sx, sy, ox, oy)) * (-0.15)

                # Mild tie-break: prefer moving (avoid pure stalling unless optimal).
                move_term = -(dx == 0 and dy == 0) * 0.3

                score = lead_term + dist_term + move_term
            else:
                # No resources: move to maximize distance from opponent (deterministic survival)
                score = (man(nx, ny, ox, oy)) * 0.2 - (abs(nx - ox) + abs(ny - oy)) * 0.0

            if score > best_score:
                best_score = score
                best = [dx, dy]

    # Fallback (shouldn't happen)
    return best if isinstance(best, list) else [0, 0]