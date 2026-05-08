def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    myc = int(observation.get("self_territory_count", 0) or 0)
    opc = int(observation.get("opponent_territory_count", 0) or 0)
    prefer_press = myc <= opc

    unclaimed = observation.get("unclaimed_cells", []) or []
    has_unclaimed = bool(unclaimed)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if prefer_press:
            t = dist(nx, ny, ox, oy)
            v = -t
        else:
            if has_unclaimed:
                # nearest unclaimed target
                tmin = None
                for p in unclaimed:
                    if isinstance(p, (list, tuple)) and len(p) >= 2:
                        tx, ty = int(p[0]), int(p[1])
                        if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                            t = dist(nx, ny, tx, ty)
                            if tmin is None or t < tmin:
                                tmin = t
                v = -(tmin if tmin is not None else 10**9)
            else:
                # fallback: expand toward opponent's vicinity
                v = -dist(nx, ny, ox, oy)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [0, 0] if best is None else [int(best[0]), int(best[1])]