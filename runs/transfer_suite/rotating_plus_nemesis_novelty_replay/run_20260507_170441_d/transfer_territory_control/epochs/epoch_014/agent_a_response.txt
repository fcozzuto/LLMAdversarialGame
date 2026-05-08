def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): blocked.add((x, y))
        except: pass

    self_set = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_set = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    edges = {0, w-1, 0, h-1}

    # Choose a deterministic target: prefer edge unclaimed; else nearest unclaimed.
    edge_targets = [c for c in unclaimed if (c[0] in (0, w-1) or c[1] in (0, h-1)) and c not in blocked]
    if edge_targets:
        tx, ty = min(edge_targets, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))
    else:
        any_targets = [c for c in unclaimed if c not in blocked]
        if any_targets:
            tx, ty = min(any_targets, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))
        else:
            # Fallback: drift toward center-ish to avoid edge mirroring.
            tx, ty = w//2, h//2

    best_delta = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        val = 0
        if (nx, ny) in opp_set:
            val += 3
        elif (nx, ny) in unclaimed:
            val += 2
        elif (nx, ny) in self_set:
            val += 0.2
        # Move toward target
        dist = abs(nx - tx) + abs(ny - ty)
        val += -0.9 * dist
        # Slightly prefer edges if target is edge; else prefer not being on edge
        on_edge = (nx in (0, w-1) or ny in (0, h-1))
        target_on_edge = (tx in (0, w-1) or ty in (0, h-1))
        val += (0.25 if target_on_edge else -0.08) * (1 if on_edge else 0)
        # Avoid getting too close to opponent
        val += -0.06 * (abs(nx-ox) + abs(ny-oy))
        if val > best_val or (val == best_val and (dx, dy) < best_delta):
            best_val = val
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]