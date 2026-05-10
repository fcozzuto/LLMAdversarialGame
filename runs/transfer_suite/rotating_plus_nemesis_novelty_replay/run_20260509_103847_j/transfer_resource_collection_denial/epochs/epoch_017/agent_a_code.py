def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Choose best target for us; if opponent is closer, switch to best resource where we have relative advantage.
    scored = []
    for r in resources:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        rel = od - sd  # larger means we are closer
        scored.append((rel, sd, od, r[0], r[1], r))

    # Prefer taking something we can reach first; if none, take closest regardless.
    max_rel = max(s[0] for s in scored)
    if max_rel > 0:
        scored.sort(key=lambda t: (-t[0], t[1], t[3], t[4]))
    else:
        scored.sort(key=lambda t: (t[1], t[3], t[4]))
    target = scored[0][-1]

    # Step: move to neighbor that minimizes our distance to target; avoid making it easier for opponent too much.
    # Tie-break deterministically by (dx,dy) order.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nds = man((nx, ny), target)
        nod = man((ox, oy), target)
        # If we don't improve, prefer staying; also slightly penalize reducing opponent distance to their likely capture.
        key = (nds, nds - od, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]