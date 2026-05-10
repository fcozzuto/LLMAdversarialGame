def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = list(unclaimed) if unclaimed else []
    if not targets:
        # If no unclaimed, chase opponent territory borders; otherwise hold.
        targets = list(op_terr)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        pos = (nx, ny)
        base = 0

        if pos in op_terr:
            base += 120  # high value: flipping opponent control
        elif pos in unclaimed:
            base += 70   # strong: claim new space
        elif pos in my_terr:
            base += 10   # small: consolidate

        # Move toward best target (deterministic via min key).
        if targets:
            t = min(targets, key=lambda p: (md(pos, p), abs(p[0] - ox) + abs(p[1] - oy)))
            dist_to_target = md(pos, t)
            base += max(0, 40 - dist_to_target)

        # Push away from opponent when we can't flip; otherwise allow proximity for capture.
        dist_to_opp = md(pos, (ox, oy))
        if pos not in op_terr:
            base += dist_to_opp * 0.5

        # Discourage bouncing into our own interior when unclaimed exist.
        if targets and pos in my_terr:
            # Check if any neighbor is unclaimed or opponent-territory (frontier).
            frontier = False
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    ex, ey = nx + ax, ny + ay
                    if inb(ex, ey) and (ex, ey) not in obstacles:
                        if (ex, ey) in unclaimed or (ex, ey) in op_terr:
                            frontier = True
                            break
                if frontier:
                    break
            if not frontier:
                base -= 12

        # Small preference for staying only if clearly best.
        if dx == 0 and dy == 0:
            base -= 1

        if base > best_val:
            best_val = base
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]