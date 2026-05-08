def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
        elif isinstance(o, dict) and "x" in o and "y" in o:
            x, y = int(o["x"]), int(o["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    best = None
    bestv = None
    # Tie-break order prefers non-diagonal -> diagonal -> stay, but deterministic by key.
    pref = {(-1, -1): 3, (0, -1): 1, (1, -1): 3, (-1, 0): 1, (0, 0): 2, (1, 0): 1, (-1, 1): 3, (0, 1): 1, (1, 1): 3}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        md = abs(nx - ox) + abs(ny - oy)
        cd = max(abs(nx - ox), abs(ny - oy))
        # Pursuer: minimize distance; Evader: maximize distance and avoid getting aligned too easily.
        if is_evader:
            # Slightly reward moving to more "cornered" positions and reducing approach on either axis.
            corner_boost = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            v = (md, cd, corner_boost)
            better = (bestv is None) or (v > bestv) or (v == bestv and pref[(dx, dy)] < pref[best[0:2]])
        else:
            v = (-md, -cd)
            better = (bestv is None) or (v > bestv) or (v == bestv and pref[(dx, dy)] < pref[best[0:2]] if best else False)
        if better:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]