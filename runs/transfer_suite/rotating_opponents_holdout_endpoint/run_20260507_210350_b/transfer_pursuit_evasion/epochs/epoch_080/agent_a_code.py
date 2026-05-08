def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or role == "pursuer"

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    prefer = corners[phase]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_for(nx, ny):
        # If pursuer: minimize distance; if evader: maximize distance.
        d = abs(nx - ox) + abs(ny - oy)
        if is_pursuer:
            return -d
        return d

    target = prefer
    if not is_pursuer:
        # Evader: choose corner with maximal distance, tie-breaker by phase corner.
        best = prefer
        bestd = -1
        for c in corners:
            cd = abs(c[0] - ox) + abs(c[1] - oy)
            if cd > bestd:
                bestd = cd
                best = c
        target = best

    # Deterministic detour: consider one-step toward target/opp with obstacle avoidance.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = score_for(nx, ny)

        if not is_pursuer:
            # Add strong preference for moving closer to chosen target.
            td = abs(nx - target[0]) + abs(ny - target[1])
            curtd = abs(sx - target[0]) + abs(sy - target[1])
            val = val * 10 - td + (1 if td < curtd else 0)
        else:
            # Pursuer: add mild preference for moving toward opponent.
            curd = abs(sx - ox) + abs(sy - oy)
            nd = abs(nx - ox) + abs(ny - oy)
            val = val * 10 + (1 if nd < curd else 0)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all candidate moves were blocked, stay still.
    return [int(best_move[0]), int(best_move[1])]