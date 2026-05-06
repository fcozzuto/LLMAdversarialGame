def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in blocked:
                rpos.append((x, y))
        elif isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
                if inb(x, y) and (x, y) not in blocked:
                    rpos.append((x, y))

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # Nemesis/Shadow counter: if opponent is closer to the nearest resource, switch to a resource
    # that reduces our "catch-up gap" and increases their next-step cost.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        my_adj = cheb(nx, ny, ox, oy)
        danger = 1.0 if my_adj <= 1 else 0.0

        # Baseline: closest resource distances from current/next positions
        best_target_score = -10**9
        for rx, ry in rpos:
            my_now = man(sx, sy, rx, ry)
            op_now = man(ox, oy, rx, ry)
            my_next = man(nx, ny, rx, ry)
            op_next = man(ox, oy, rx, ry)  # opponent won't move in this eval step

            # If opponent is currently closer, prefer targets where we reduce gap the most.
            # Otherwise just go for closest.
            gap_now = op_now - my_now
            gap_next = op_next - my_next
            reduce_gap = gap_now - gap_next  # positive means we catch up
            reach = (my_next == 0)

            # Opponent interference: being closer to a resource can force them to divert.
            # We reward making their distance to that resource relatively larger than ours.
            rel = op_next - my_next

            score = 0
            if gap_now > 0:
                score += 6.0 * reduce_gap
                score += 2.0 * rel
            else:
                score += -1.2 * my_next
                score += 0.6 * rel

            score += 3.5 * reduce_gap if reach else 0.0
            score += 0.2 * (1.0 if (rx + ry) % 2 == (nx + ny) % 2 else 0.0)

            if score > best_target_score:
                best_target_score = score

        # Overall: capture pressure over danger; deterministic tie-break via tuple ordering.
        overall = best_target_score - 2.5 * danger
        key = (-overall, dx, dy)  # maximize overall
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]