def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursu" in self_role) or ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist2(nx, ny, ox, oy)

        if pursuer:
            # Push toward opponent; small bias toward continuing in its direction (lead step).
            lx = ox + (1 if ox > sx else (-1 if ox < sx else 0))
            ly = oy + (1 if oy > sy else (-1 if oy < sy else 0))
            if not valid(lx, ly):
                lx, ly = ox, oy
            score = -(d) - 0.1 * dist2(nx, ny, lx, ly)
        else:
            # Evade: maximize distance; also prefer corners (deterministic tie-breaker).
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            corner_score = max(dist2(nx, ny, cx, cy) for cx, cy in corners)
            score = d + 0.01 * corner_score

        candidates.append((score, -d, dx, dy))
    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]