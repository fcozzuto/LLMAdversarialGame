def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs_list = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obs_list)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells", []) or []
    best_t = None
    best_td = None
    for p in unclaimed:
        tx, ty = p[0], p[1]
        if (tx, ty) in obs or not inb(tx, ty):
            continue
        d = abs(tx - ox) + abs(ty - oy)
        if best_t is None or d < best_td or (d == best_td and (tx, ty) < best_t):
            best_t, best_td = (tx, ty), d

    if best_t is None:
        best_t = (ox, oy)
    tx, ty = best_t

    best_m = None
    best_md = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs or not inb(nx, ny):
            continue
        md = abs(nx - tx) + abs(ny - ty)
        if best_m is None or md < best_md or (md == best_md and (dx, dy) < best_m):
            best_m, best_md = (dx, dy), md

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]