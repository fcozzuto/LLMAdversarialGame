def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    rem = observation.get("remaining_resource_count", None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if abs(dx) > abs(dy):
            return abs(dx)
        return abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None

    targets = resources if resources else [(w // 2, h // 2)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # If standing on/near a resource, prioritize it
        if resources:
            d_self = min(cheb(nx, ny, tx, ty) for tx, ty in targets)
            d_opp = min(cheb(ox, oy, tx, ty) for tx, ty in targets)
            # Prefer moves that reduce our distance to resources relative to opponent
            v = (d_opp - d_self) * 100 - d_self
        else:
            # Fallback: move toward center while avoiding opponent
            cx, cy = w // 2, h // 2
            v = -cheb(nx, ny, cx, cy) * 10 + cheb(nx, ny, ox, oy) * 2
        # Strongly avoid immediate contact with opponent if possible
        if cheb(nx, ny, ox, oy) <= 1 and (resources or rem):
            v -= 80
        if best is None or v > bestv:
            best = (dx, dy)
            bestv = v

    return list(best if best is not None else (0, 0))