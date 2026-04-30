def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    bestd = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < bestd:
            bestd = d
            target = (rx, ry)

    if target is None:
        # fallback: move away from opponent if possible, else random among options deterministically
        target = (sx, sy)

    rx, ry = target
    cur_op = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_score = 10**18

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_t = cheb(nx, ny, rx, ry)
            d_o = cheb(nx, ny, ox, oy)
            # Prefer closer to target; strongly discourage getting near opponent
            score = d_t + max(0, 3 - d_o) * 2 + (0 if d_o >= cur_op else (cur_op - d_o)) * 0.5
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    # if all moves blocked, try staying or any valid adjacent deterministic move
    if best_score == 10**18:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]