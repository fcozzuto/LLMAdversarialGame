def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def near_obst_pen(x, y):
        # small deterministic penalty for stepping adjacent to obstacles
        pen = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 1
        return pen

    if not resources:
        # Move to improve space between us and opponent while avoiding obstacles
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer increasing distance to opponent (deterministic)
            v = man(nx, ny, ox, oy) - 0.2 * near_obst_pen(nx, ny)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Score moves by best "resource swing": (opp distance - me distance), plus tie-break to deny closer access
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) != (sx, sy):
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

        # Evaluate a few best candidate resources deterministically (closest to either agent)
        scored = []
        for rx, ry in resources:
            dme = man(nx, ny, rx, ry)
            dop = man(ox, oy, rx, ry)
            # If we're closer, swing is positive; if farther, swing is negative.
            swing = dop - dme
            # Additional bias: resources where opponent is already close are more dangerous; prioritize denying.
            danger = 0.0
            if dop <= 2:
                danger = 6.0
            scored.append((swing - 0.3 * dme - danger, dme, dop, rx, ry))
        scored.sort(reverse=True, key=lambda t: (t[0], -t[1], t[2]))

        # Main value: top resource swing, plus mild consideration of the second to avoid bad single-target traps.
        v = 0.0
        for i in range(min(3, len(scored))):
            swing, dme, dop, rx, ry = scored[i]
            # If opponent is also close and swing small, still give some value to securing earlier.
            v += (10.0 * swing) - (1.0 * max(0, dme - dop)) - 0.15 * near_obst_pen(nx, ny)
        # Tie-break: prefer reducing distance to top target and staying valid
        if v > best_val + 1e-9:
            best_val = v
            best_move = [dx, dy]
        elif abs(v - best_val) <= 1e-9:
            # Deterministic tie-break: closer to opponent decreases their options? Instead, prefer moving to reduce our distance to top target.
            # Use the computed best target from current move.
            d_top = scored[0][1] if scored else 10**9
            d_best_top = None
            if best_move != [0, 0] or True:
                # Recompute for best_move position quickly
                bdx, bdy = best_move
                bx, by = sx + bdx, sy + bdy
                bt = 10**9
                for rx, ry in resources:
                    bt = min(bt, man(bx, by, rx, ry))
                d_best_top = bt
            if d_top < d_best_top:
                best_move = [dx, dy]

    return best_move