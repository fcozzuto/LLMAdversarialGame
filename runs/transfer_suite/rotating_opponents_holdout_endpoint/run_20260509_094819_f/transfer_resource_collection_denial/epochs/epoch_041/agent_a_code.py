def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        total = 0
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            contested = 1 if od <= sd else 0  # prefer resources we can reach before/at opponent
            adv = (od - sd)  # positive means opponent farther (good for us)

            # Strongly prioritize contested advantage, then closeness.
            val = (adv * 200) + (contested * 80) - sd

            # Mild tie-breaking: also prefer moving toward resources that aren't behind obstacles (local proxy: avoid if obstacle blocks direct step).
            if sd == 0:
                val += 10000  # immediate collection

            total += val

        # Deterministic tie-break by preferring lower |dx|+|dy| then lexicographic (dx,dy)
        tie = (abs(dx) + abs(dy), dx, dy)
        if best_val is None or total > best_val or (total == best_val and tie < (abs(best[0]) + abs(best[1]), best[0], best[1])):
            best_val = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]