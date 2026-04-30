def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0) or 8
    H = int(observation.get("grid_height", 0) or 0) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [W - 1, H - 1])

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    oppd = man(sx, sy, ox, oy)

    if resources:
        # Prefer moves that make us relatively closer than the opponent to some resource.
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = 10**9
            for rx, ry in resources:
                our_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                # Lower is better: prioritize making us closer than opponent.
                s = (our_d - opp_d) * 10 + our_d
                if s < score:
                    score = s
            # Small deterministic tie-breaker: also consider staying out of immediate proximity if tied.
            score2 = score * 1000 + abs((man(nx, ny, ox, oy) - oppd))
            cand = (score2, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    # No resources: move toward center while not moving into obstacles; tie-break by reducing distance to opponent.
    cx, cy = W // 2, H // 2
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        center_d = man(nx, ny, cx, cy)
        opp_d = man(nx, ny, ox, oy)
        cand = (center_d * 1000 + opp_d, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[1], best[2]]