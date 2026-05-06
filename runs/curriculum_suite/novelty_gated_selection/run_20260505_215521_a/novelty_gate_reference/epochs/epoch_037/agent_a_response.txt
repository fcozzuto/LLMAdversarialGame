def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = man(nx, ny, ox, oy)
            if score > best[2]:
                best = (dx, dy, score)
        return [int(best[0]), int(best[1])]

    # Pick a resource we can "secure": where (opponent_dist - our_dist) is largest.
    best_t = resources[0]
    best_gap = -10**9
    for x, y in resources:
        d_me = man(sx, sy, x, y)
        d_op = man(ox, oy, x, y)
        gap = d_op - d_me
        tie = -d_me * 0.01
        val = gap + tie
        if val > best_gap:
            best_gap = val
            best_t = (x, y)

    tx, ty = best_t

    # Move: minimize distance to target; keep some distance from opponent to reduce diagonal probing.
    best_move = (0, 0, 10**9, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        # Strongly prefer not being too close to opponent while progressing.
        danger = 0
        if d_o <= 1:
            danger = 200
        elif d_o == 2:
            danger = 60
        elif d_o == 3:
            danger = 20
        score1 = d_t + danger
        score2 = d_o
        if (score1 < best_move[2]) or (score1 == best_move[2] and score2 > best_move[3]):
            best_move = (dx, dy, score1, score2)

    return [int(best_move[0]), int(best_move[1])]