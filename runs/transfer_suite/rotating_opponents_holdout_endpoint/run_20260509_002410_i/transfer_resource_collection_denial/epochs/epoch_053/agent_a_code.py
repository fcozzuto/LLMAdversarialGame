def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    tx = observation.get("turn_index", 0)

    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # diagonal allowed: use Chebyshev distance
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def valid_cell(x, y):
        return inb(x, y) and (x, y) not in obstacles

    candidates = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid_cell(rx, ry):
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prioritize resources we can reach first; otherwise, reduce opponent's lead.
        slack = do - ds
        # Secondary: prefer closer to us and a deterministic parity filter.
        parity = (rx + ry + int(tx)) & 1
        key = (1 if slack > 0 else 0, slack, -ds, -parity)
        candidates.append((key, rx, ry))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    _, rx, ry = candidates[0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid_cell(nx, ny):
                # Prefer steps that reduce distance to target; deterministic tie-break via (dx,dy).
                nd = dist((nx, ny), (rx, ry))
                cd = dist((sx, sy), (rx, ry))
                moves.append((cd - nd, -nd, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(reverse=True)
    _, _, dx, dy = moves[0]
    return [int(dx), int(dy)]