def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    role = observation.get("self_role") or ""
    is_evader = (role.lower() == "evader")

    def score_for(x, y):
        d = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        # Pursuer wants smaller distance; evader wants larger distance.
        return (-d if not is_evader else d)

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in ob:
            continue

        # Prefer immediate capture (distance 0) for pursuer; prefer maximizing escape for evader.
        dman = abs(nx - ox) + abs(ny - oy)
        cap_bonus = -1000000 if (not is_evader and dman == 0) else (1000000 if (is_evader and dman == 1) else 0)

        # Secondary preference: move in the general direction of/away from opponent.
        dir_pref = -((dx == 0 and dy == 0) * 5)
        if not is_evader:
            step_to = (0 if dx == 0 else 1) + (0 if dy == 0 else 1)
            dir_pref += step_to
        else:
            away = (abs(nx - ox) + abs(ny - oy))
            dir_pref += away * 0.01

        key = (score_for(nx, ny), (abs(dx) + abs(dy)), 0 if (dx == 0 and dy == 0) else 1, cap_bonus, dir_pref, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]