def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    tr = int(observation.get("remaining_resource_count", 999) or 999)
    endgame = tr <= 2 or (int(observation.get("turns_remaining", 0) or 0) <= 6)
    stay = (0, 0)
    best_move = stay
    best_score = -10**18

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [stay]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = -10**18
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - dm  # positive is good
            # Prefer grabbing first; otherwise maximize lead and closeness.
            s = lead * (100 if endgame else 20) - dm - (0 if endgame else abs(lead) == 0)
            if s > score:
                score = s
        if score > best_score or (score == best_score and (dx, dy) == stay):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]