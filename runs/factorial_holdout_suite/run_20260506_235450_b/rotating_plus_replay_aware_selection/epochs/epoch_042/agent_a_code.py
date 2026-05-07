def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def best_target_from(posx, posy):
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(posx, posy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # race advantage; prefer wins, then faster, then closer to center slightly
            win = (do - ds)
            center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
            val = win * 1000 - ds * 10 - center
            if best is None or val > best[0]:
                best = (val, ds, do, rx, ry)
        return best

    # If we can immediately take a resource, prioritize it
    for dx, dy, nx, ny in legal:
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if nx == rx and ny == ry:
                # still ensure we beat opponent timing if possible
                if cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry) >= 0:
                    return [dx, dy]
                break

    best_move = None
    for dx, dy, nx, ny in legal:
        tgt = best_target_from(nx, ny)
        # small position preference: move toward best potential target
        if tgt is None:
            continue
        val = tgt[0]
        # discourage stepping away if equal race
        cur_best = best_target_from(sx, sy)
        if cur_best is not None and val == cur_best[0]:
            val = val - cheb(nx, ny, cur_best[3], cur_best[4]) * 0.001
        if best_move is None or val > best_move[0] or (val == best_move[0] and (dx, dy) < best_move[1]):
            best_move = (val, (dx, dy))
    if best_move is None:
        return [0, 0]
    return [int(best_move[1][0]), int(best_move[1][1])]