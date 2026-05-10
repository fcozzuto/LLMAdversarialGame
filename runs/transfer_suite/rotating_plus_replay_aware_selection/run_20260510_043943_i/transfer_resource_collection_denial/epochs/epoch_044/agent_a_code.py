def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def pick_target():
        if not resources:
            return (int((w - 1) / 2), int((h - 1) / 2))
        best_r = resources[0]
        best_v = -10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            v = (do - ds) * 1000 - ds
            if ds == 0:
                v += 10**9
            if ds == 1:
                v += 5 * 10**5
            # small deterministic tie-breaker
            v += -(rx * 7 + ry * 11) * 1e-6
            if v > best_v:
                best_v = v
                best_r = (rx, ry)
        return best_r

    tx, ty = pick_target()

    # If already on target, try to deny opponent by staying unless an adjacent is also immediately winning.
    if sx == tx and sy == ty and resources:
        immediate = None
        for rx, ry in resources:
            if (rx, ry) != (tx, ty):
                ds = man(sx, sy, rx, ry)
                do = man(ox, oy, rx, ry)
                if ds == 1 and do > 1:
                    immediate = (rx, ry)
                    break
        if immediate:
            tx, ty = immediate

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # race: prefer reducing my distance and increasing opponent's relative advantage
        score = (do - ds) * 1000 - ds
        if nx == tx and ny == ty:
            score += 10**9
        # avoid moving into positions where opponent is closer to the target than we are
        if man(ox, oy, tx, ty) <= ds:
            score -= 200
        # slight preference to move generally toward target to ensure progress
        score += -(abs(nx - tx) + abs(ny - ty)) * 0.01
        # obstacle-aware tie-breaker
        score += 0.0 if (nx, ny) in obstacles else 0.000001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all candidate moves blocked, return stay.
    return [int(best_move[0]), int(best_move[1])]