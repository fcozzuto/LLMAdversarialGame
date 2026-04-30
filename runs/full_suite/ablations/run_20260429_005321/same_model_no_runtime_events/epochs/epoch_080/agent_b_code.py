def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        score = 0
        if resources:
            best_margin = -10**18
            best_tie = 10**18
            for rx, ry in resources:
                md = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                margin = od - md  # positive means we are closer than opponent (or tie)
                tiebreak = md
                if margin > best_margin or (margin == best_margin and tiebreak < best_tie):
                    best_margin = margin
                    best_tie = tiebreak
            # Encourage being closer than opponent to some resource
            score += best_margin * 1000
            # Secondary: reduce our distance to that winning resource
            score -= best_tie
            # Tertiary: keep options open by preferring not-too-far from multiple resources
            near_count = 0
            for rx, ry in resources:
                if dist(nx, ny, rx, ry) <= best_tie + 1:
                    near_count += 1
            score += near_count * 3
        else:
            # No visible resources: drift toward center while avoiding opponent if adjacent
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = -dist(nx, ny, cx, cy)
            if dist(nx, ny, ox, oy) <= 1:
                score -= 50

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move