def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    evading = ("evad" in self_role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    ti = int(observation.get("turn_index", 0) or 0)
    phase_corner = corners[ti % 4]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    target = far_corner if evading else phase_corner

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def adj_block_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move, best_score = (0, 0), None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        opp_dist = manh(nx, ny, ox, oy)
        tgt_dist = manh(nx, ny, target[0], target[1])
        block = adj_block_count(nx, ny)

        if evading:
            score = (opp_dist * 10) + (tgt_dist * -1) - (block * 2)
        else:
            score = (-opp_dist * 10) + (tgt_dist * -0.2) - (block * 2)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move