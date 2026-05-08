def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                oset.add((int(p[0]), int(p[1])))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("pursuer" in opponent_role) or ("pursuit" in opponent_role)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in oset:
                candidates.append((dx, dy))

    def dist2(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)
        if is_pursuer:
            toward = (0 if ox == sx else (1 if ox > sx else -1), 0 if oy == sy else (1 if oy > sy else -1))
            align = dx * toward[0] + dy * toward[1]
            score = -d * 100 + align
        else:
            # Evader: go far and prefer increasing either x/y distance deterministically
            towardx = 0 if ox == nx else (-1 if ox > nx else 1)
            towardy = 0 if oy == ny else (-1 if oy > ny else 1)
            align = dx * towardx + dy * towardy
            score = d * 100 + align

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: lexicographically prefer dx, then dy toward general direction
            if (dx, dy) > best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]