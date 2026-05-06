def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def center_score(x, y):
        d = abs(x - cx) + abs(y - cy)
        return -d  # closer to center is better

    def nearest_info(px, py):
        if not resources:
            return 10**9, 0
        best_d = 10**9
        best_c = -10**9
        for rx, ry in resources:
            d = manh(px, py, rx, ry)
            c = center_score(rx, ry)
            if d < best_d or (d == best_d and c > best_c):
                best_d, best_c = d, c
        return best_d, best_c

    opp_d, opp_c = nearest_info(ox, oy)

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        self_d, self_c = nearest_info(nx, ny)
        if resources:
            # Prefer taking nearer resources while reducing opponent advantage; center bias helps vs edge patrol
            score = (opp_d - self_d) * 3.0 + (self_c - opp_c) * 0.8 - manh(nx, ny, ox, oy) * 0.05
        else:
            score = manh(nx, ny, ox, oy) + center_score(nx, ny)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]