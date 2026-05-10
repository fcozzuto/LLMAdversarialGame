def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    near_cells = unclaimed[:50] if unclaimed else []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        if (nx, ny) in self_terr:
            score += 4
        if (nx, ny) in op_terr:
            score -= 2
        if (nx, ny) in map(tuple, near_cells):
            score += 30

        if near_cells:
            d_self = min((manh(nx, ny, cx, cy) for cx, cy in near_cells), default=10**9)
            score += 20 - min(d_self, 20)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score += 10 - manh(nx, ny, cx, cy)

        d_op = manh(nx, ny, ox, oy)
        score += 2 if d_op >= 2 else -2

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]