def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    rem = observation.get("remaining_resource_count")
    if rem is None:
        rem = len(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Prefer collecting resources: lower distance is better; being on a resource is best.
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            on_res = 1 if (nx, ny) in resources else 0
        else:
            dmin = 10**6
            on_res = 0

        # Prefer moving away from opponent when close; otherwise go after resources.
        dop = cheb(nx, ny, ox, oy)
        safe = 0
        if dop <= 2:
            safe = dop  # larger dop is safer

        # Combine: maximize score deterministically.
        score = 0
        if rem:
            score += on_res * 10000
        score += (0 if resources else -1) * 0
        score += (1000 - dmin * 10) + safe * 50

        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]