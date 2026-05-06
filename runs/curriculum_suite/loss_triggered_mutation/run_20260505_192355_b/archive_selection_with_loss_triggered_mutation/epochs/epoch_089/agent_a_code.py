def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Global potential: sum of per-resource "who's closer" advantages, favoring capturing contested resources.
        pot = 0
        min_self = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if od < 10**9:
                # Boost resources where we can get closer than opponent; discount far ones to keep it local.
                diff = od - sd
                if diff > 0:
                    pot += (diff * 10) // (1 + sd)
                else:
                    pot += (diff * 2) // (1 + sd)
            if sd < min_self:
                min_self = sd
            if od < min_opp:
                min_opp = od
        # Repel opponent to reduce blocking/collisions; also favor moving toward the closest "net-good" area.
        pot += (min_opp - min_self) * 3
        if cheb(nx, ny, ox, oy) <= 1:
            pot -= 50
        # Deterministic tie-break: higher pot, then smaller min_self, then lex on (dx,dy)
        key = (pot, -min_self, -min_opp, dx, dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]