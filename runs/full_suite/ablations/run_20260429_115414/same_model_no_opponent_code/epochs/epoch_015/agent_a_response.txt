def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rs = []
    for x, y in resources:
        x, y = int(x), int(y)
        if free(x, y):
            rs.append((x, y))

    if not rs:
        return [0, 0]

    # Select target that I am relatively closer to (and deterministic tie-break)
    best = None
    for x, y in rs:
        md = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        score = (od - md) * 100 - md
        key = (score, -x, -y)
        if best is None or key > best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            myd = cheb(nx, ny, tx, ty)
            oppd = cheb(ox, oy, tx, ty)
            # Prefer reducing my distance; also prefer states where I’m not letting opponent get relatively closer
            lead = (oppd - myd)
            # Slightly avoid obstacle-adjacency without getting stuck
            adj = 0
            for ax, ay in obs:
                if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                    adj += 1
            key = (lead * 100 - myd * 2 - adj, -abs(nx - tx) - abs(ny - ty), dx, dy)
            moves.append((key, (dx, dy)))

    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][1][0]), int(moves[0][1][1])]