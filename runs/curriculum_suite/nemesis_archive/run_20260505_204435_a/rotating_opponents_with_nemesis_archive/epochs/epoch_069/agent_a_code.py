def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                px, py = q[0], q[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            px, py = r[0], r[1]
        else:
            continue
        if inb(px, py) and (px, py) not in blocked:
            rpos.append((px, py))

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_move = (0, 0)

    # Opponent "shadow": assume it moves toward its nearest resource (myopic)
    opp_targets = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            nearest = min(abs(nx - rx) + abs(ny - ry) for rx, ry in rpos)
            opp_targets.append((nearest, nx, ny))
    if opp_targets:
        opp_next = min(opp_targets)[1:3]
    else:
        opp_next = (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nearest_self = min(abs(nx - rx) + abs(ny - ry) for rx, ry in rpos)
        # Prefer staying away from opponent's next position while still pushing resources
        opp_dist = abs(nx - opp_next[0]) + abs(ny - opp_next[1])

        # Local richness: count nearby resources within 3 manhattan steps
        near_cnt = 0
        for rx, ry in rpos:
            if abs(nx - rx) + abs(ny - ry) <= 3:
                near_cnt += 1

        # Combine: primary is resource proximity, then opponent separation, then richness
        # Convert to a lex-sortable key (smaller is better)
        key = (nearest_self, -opp_dist, -near_cnt, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]