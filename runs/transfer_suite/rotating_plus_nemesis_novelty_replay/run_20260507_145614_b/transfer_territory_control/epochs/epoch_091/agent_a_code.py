def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        for p in observation.get("resources") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    best = None
    best_score = -10**18

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        edge = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
        oppd = man(nx, ny, ox, oy)
        if targets:
            mind = min(man(nx, ny, tx, ty) for tx, ty in targets)
            score = -mind + 0.2 * oppd + 0.1 * edge
        else:
            score = 0.3 * oppd + 0.1 * edge
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]
    return best