def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def adj_block(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles: c += 1
        return c

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]; bestv = -10**18
        for i, (rx, ry) in enumerate(resources):
            dme = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Prefer places we can reach sooner; if tied, prefer farther from opponent line/area.
            v = (dop - dme) * 12.0 - dme * 0.7
            # Discourage hugging obstacles
            v -= adj_block(rx, ry) * 1.8
            # Small deterministic tie-breaker: center preference then index
            v += -0.02 * (abs(rx - w / 2) + abs(ry - h / 2)) - 1e-6 * i
            if v > bestv:
                bestv = v; best = (rx, ry)
        return best

    tx, ty = best_target()

    # Choose move that improves relative distance to target and avoids obstacles.
    bestm = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        dme2 = cheb(nx, ny, tx, ty)
        dme1 = cheb(sx, sy, tx, ty)
        dop = cheb(ox, oy, tx, ty)
        # Relative progress + safety + don't wander
        v = (dop - dme2) * 10.0 - dme2 * 0.9
        v += (dme1 - dme2) * 2.4
        v -= adj_block(nx, ny) * 1.5
        # Mild preference for not oscillating too hard: deterministic bias by coordinate sum
        v += -1e-4 * ((nx + ny) % 7)
        if v > bestv:
            bestv = v; bestm = (dx, dy)

    # If somehow no free move found (edge cases), stay still.
    return [int(bestm[0]), int(bestm[1])]