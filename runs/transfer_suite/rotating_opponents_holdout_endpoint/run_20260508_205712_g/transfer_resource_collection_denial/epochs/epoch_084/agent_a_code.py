def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    bias_x = 1 if sx < (W - 1) / 2 else -1
    bias_y = 1 if sy < (H - 1) / 2 else -1

    scored_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best = 10**9
        for rx, ry in res:
            d_me = dist((nx, ny), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Encourage getting there before opponent and push toward our half.
            score = d_me * 5 - d_opp * 3 - (rx - (W - 1) / 2) * bias_x * 0.05 - (ry - (H - 1) / 2) * bias_y * 0.05
            if score < best:
                best = score
        # Small penalty for moving away from the closer half to reduce oscillation
        oscill = -((dx != 0) * bias_x * dx + (dy != 0) * bias_y * dy) * 0.01
        scored_moves.append((best + oscill, dx, dy))

    scored_moves.sort()
    return [int(scored_moves[0][1]), int(scored_moves[0][2])]