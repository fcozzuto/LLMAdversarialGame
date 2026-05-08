def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "")
    opp_role = str(observation.get("opponent_role", "") or "")
    if "evader" in self_role.lower() and "pursuer" in opp_role.lower():
        role = "evader"
    elif "pursuer" in self_role.lower() and "evader" in opp_role.lower():
        role = "pursuer"
    else:
        scores = observation.get("scores", None)
        my_s = 0
        op_s = 0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0))) or 0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0))) or 0
        elif isinstance(scores, (list, tuple)) and len(scores) >= 2:
            my_s, op_s = scores[0] or 0, scores[1] or 0
        role = "pursuer" if my_s <= op_s else "evader"

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            if role == "pursuer":
                edge_bonus = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
                score = -dist + (0.15 if edge_bonus else 0.0)
            else:
                corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
                tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
                corner_dist = abs(nx - tx) + abs(ny - ty)
                edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
                # Prefer staying near a wall (if possible) while increasing distance from pursuer
                score = dist + (0.35 if edge else 0.0) - 0.02 * corner_dist
            candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]