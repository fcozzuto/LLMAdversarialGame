def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def pick_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd == 0 and od == 0:
                key = (10**9, 0, -(rx * 9 + ry))
            else:
                # Prefer resources we can reach earlier; then closer.
                key = (od - sd, -sd, -(rx * 9 + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = pick_target()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # Prefer reducing distance to target, and gaining distance advantage vs opponent.
        # Slightly penalize closeness to obstacles to avoid getting stuck.
        obst_pen = 0
        for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny-1), (nx-1, ny+1), (nx+1, ny+1)]:
            if (ax, ay) in obs:
                obst_pen += 2
        score = (-(sd2), (od2 - sd2), -(obst_pen), -(dx*dx + dy*dy), -(dx + 2*dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all legal moves blocked (should be rare), stay still.
    return [int(best_move[0]), int(best_move[1])]