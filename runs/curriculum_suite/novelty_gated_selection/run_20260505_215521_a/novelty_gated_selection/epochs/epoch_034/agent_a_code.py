def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obst)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    # Targeting logic (different from pure advantage swapping): combine "opp urgency" + center control.
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_r = None
    best_r_score = None
    for rx, ry in resources:
        opp_d = man(ox, oy, rx, ry)
        our_d = man(sx, sy, rx, ry)
        center_d = abs(rx - cx) + abs(ry - cy)
        urgency = -opp_d  # prioritize resources opponent can reach quickly
        if our_d == 0:
            lead = 9999
        else:
            lead = opp_d - our_d  # positive means we are closer
        score = (urgency, center_d, lead)
        if best_r is None or score > best_r_score:
            best_r_score = score
            best_r = (rx, ry)

    tx, ty = best_r

    # Decide move by evaluating next-state: minimize our distance to the chosen target, but add a "block" term.
    # Block term: also discourages moving toward cells that increase our distance to opponent-target relation.
    best_move = (0, 0)
    best_val = None
    opp_d_now = man(ox, oy, tx, ty)

    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        our_d = man(nx, ny, tx, ty)
        opp_d_next = man(ox, oy, tx, ty)
        # prefer moves that shorten our path; if already competitive, also drift toward center slightly
        center_pref = abs(nx - cx) + abs(ny - cy)
        block = (opp_d_now - opp_d_next)  # typically 0, but keeps structure deterministic
        val = (our_d, center_pref, -block, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]