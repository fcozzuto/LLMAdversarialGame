def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            tx, ty = r[0], r[1]
            if inb(tx, ty) and (tx, ty) not in obs:
                ds = abs(sx - tx) + abs(sy - ty)
                do = abs(ox - tx) + abs(oy - ty)
                # Prefer cells where we are closer; if tie, prefer larger opponent lead disadvantage
                targets.append(((ds - do), ds, tx, ty))
    # If no valid resources, move away from opponent toward center
    if not targets:
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        targets.sort()  # smallest (ds-do), then closest
        _, _, tx, ty = targets[0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        # Greedy on winning margin after the move: (opp_dist - self_dist), tie-break by self_dist then toward target
        ns = abs(nx - tx) + abs(ny - ty)
        no = abs(ox - tx) + abs(oy - ty)
        margin = no - ns
        key = (-margin, ns, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]