def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Pick a target biased away from opponent (edge/corner harvesting to beat center-rush)
    best_r = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        dm = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if best_r is None:
            best_r = (rx, ry)
            best_key = (do - dm, do)
            continue
        key = (do - dm, do)
        if key > best_key:
            best_r = (rx, ry)
            best_key = key

    rx, ry = best_r
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    opp_now = man(ox, oy, rx, ry)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dm_next = man(nx, ny, rx, ry)
        do_next = man(ox, oy, rx, ry)  # opponent doesn't move this turn; keep consistent
        cur_dm = man(sx, sy, rx, ry)
        step_pen = 0 if (dx == 0 and dy == 0) else 1
        # Encourage getting closer to target, while keeping opponent farther from us along that direction
        opp_gap = man(ox, oy, nx, ny) - man(ox, oy, sx, sy)
        score = (-dm_next) + 0.10 * (do_next - opp_now) - 0.05 * step_pen - 0.20 * opp_gap
        # Slightly prefer not moving into the opponent's vicinity
        if man(nx, ny, ox, oy) <= 1:
            score -= 1.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]