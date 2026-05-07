def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def clamp(x, lo, hi):
        if x < lo: return lo
        if x > hi: return hi
        return x

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx = sx + dx
        ny = sy + dy
        if (nx < 0 or nx >= w or ny < 0 or ny >= h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        local_best = 10**18
        local_best_adv = -10**18
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_us  # positive if we get there earlier/equal
            if d_us < local_best:
                local_best = d_us
            if adv > local_best_adv:
                local_best_adv = adv

        # Prefer moving to immediately contact resources; otherwise, maximize advantage and reduce distance.
        near_bonus = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) == 0:
                near_bonus += 50

        # Secondary: encourage moving away from opponent if still not winning any resource contest.
        dist_to_op = cheb(nx, ny, ox, oy)

        score = 0
        score += near_bonus
        score += local_best_adv * 10
        score += -local_best
        score += dist_to_op * 0.5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]