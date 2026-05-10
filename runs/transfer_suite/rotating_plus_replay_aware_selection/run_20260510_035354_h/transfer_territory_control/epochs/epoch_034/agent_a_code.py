def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_list = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obs_list if inb(x, y))

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Target: nearest unclaimed; if none, expand toward opponent territory/frontier.
    if un_set:
        targets = list(un_set)
        targets.sort(key=lambda p: (ax - p[0]) * (ax - p[0]) + (ay - p[1]) * (ay - p[1]))
        tgt = targets[0]
        mode = "unclaimed"
    else:
        targets = list(op_set)
        if not targets:
            return [0, 0]
        targets.sort(key=lambda p: (ax - p[0]) * (ax - p[0]) + (ay - p[1]) * (ay - p[1]))
        tgt = targets[0]
        mode = "opponent"

    def score_cell(nx, ny):
        s = 0
        p = (nx, ny)
        if p in obs:
            return -10**9
        if p in un_set:
            s += 40
        if p in my_set:
            s += 5
        if p in op_set:
            # Flipping on entry is enabled: entering opponent territory is valuable.
            s += 25

        # Move toward chosen target (always beneficial).
        s += max(0, 20 - (((nx - tgt[0]) * (nx - tgt[0])) + ((ny - tgt[1]) * (ny - tgt[1]))))

        # Slight center bias to avoid cornering on empty maps.
        dc = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        s += int(10 - 0.5 * dc)

        # Prefer moves that reduce distance to nearest unclaimed (if any exist).
        if un_set and mode != "unclaimed":
            # cheap approximation: check 1-2 nearest unclaimed by using current tgt plus distance.
            d = (nx - tgt[0]) * (nx - tgt[0]) + (ny - tgt[1]) * (ny - tgt[1])
            s += max(0, 10 - d)

        # Avoid moving into tight trap: don't increase number of blocked neighbors too much.
        blocked = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if not inb(tx, ty) or (tx, ty) in obs:
                blocked += 1
        s -= blocked

        return s

    best_move = (0, 0)
    best_s = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        s = score_cell(nx, ny)
        # Deterministic tie-break: prefer staying still last (so only if strictly best),
        # then deterministic order from moves list already.
        if s > best_s:
            best_s = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]