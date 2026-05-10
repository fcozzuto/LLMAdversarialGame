def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", (0, 0))
    ax, ay = int(ax), int(ay)

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    uset = toset(self_terr)
    oset = toset(opp_terr)
    ucell = toset(unclaimed)
    obset = toset(obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Opponent "frontier": adjacent to opponent territory, not ours and in bounds and not obstacle.
    frontier = set()
    for (x, y) in oset:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in uset and (nx, ny) not in obset:
                frontier.add((nx, ny))

    # Prefer expanding into unclaimed; if none, prefer cracking opponent frontier; else defend by avoiding stepping into opponent.
    best = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        val = 0
        if (nx, ny) in ucell:
            val += 20000
        if (nx, ny) in oset:
            val += 12000
        if (nx, ny) in frontier:
            val += 8000

        # Avoid giving up territory: stepping into opponent can flip, but still discourage if not capturing new ground.
        if (nx, ny) in oset and (nx, ny) not in ucell:
            val -= 1500

        # Mildly prefer moving toward the densest local frontier/unclaimed.
        # Use local "nearby count" in a small radius for determinism and speed.
        r = 2
        near_u = 0
        near_o = 0
        for tx in range(nx - r, nx + r + 1):
            for ty in range(ny - r, ny + r + 1):
                if not inb(tx, ty):
                    continue
                if (tx, ty) in ucell:
                    near_u += 1
                elif (tx, ty) in oset:
                    near_o += 1
        val += near_u * 25 + near_o * 5

        # Keep movement somewhat directed: penalize staying too much unless there's no good option.
        if dx == 0 and dy == 0:
            val -= 30

        # Deterministic tie-break: prefer larger dx then larger dy then lexicographically smaller in original order via stable scan.
        if best is None or val > best[0] or (val == best[0] and (dx, dy) > best[1]):
            best = (val, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]