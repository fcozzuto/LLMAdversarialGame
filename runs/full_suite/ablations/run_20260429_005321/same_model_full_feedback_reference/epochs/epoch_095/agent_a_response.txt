def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def target_score(tx, ty):
        # Higher is better: prefer targets we can reach earlier than opponent
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        return (do - ds) * 10 - (tx + ty) * 0.001

    if resources:
        tx, ty = min(resources, key=lambda r: (-target_score(r[0], r[1]), r[0], r[1]))[0:2]
        tx, ty = int(tx), int(ty)
    else:
        tx, ty = w // 2, h // 2

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        # Lower is better: minimize our distance to target, prefer staying away from opponent
        val = ds * 3 - do * 0.8 + (6 - dpp(dopp)) * 0.15
        if val < best[0]:
            best = (val, dx, dy)

    if best[0] == 10**9:
        return [0, 0]
    return [int(best[1]), int(best[2])]

def dpp(d):
    if d < 0: return 0
    if d > 8: return 8
    return int(d)