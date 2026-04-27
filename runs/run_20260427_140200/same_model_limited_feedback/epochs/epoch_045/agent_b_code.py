def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        return (dx * dx + dy * dy)

    # Targeting: choose resource that is good for us and not so good for opponent
    best_t = None
    best_val = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        md = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Mild preference to resources closer to us, while denying those close to opponent
        val = md - 0.7 * od
        if best_val is None or val < best_val or (val == best_val and (rx < best_t[0] or (rx == best_t[0] and ry < best_t[1]))):
            best_val = val
            best_t = (rx, ry)
    if best_t is None:
        # Fallback: move away from opponent slightly
        tx, ty = ox, oy
    else:
        tx, ty = best_t

    # Candidate move evaluation with obstacle and "positioning to cut off" (minimize my distance; also avoid stepping into opponent line)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = dist((nx, ny), (tx, ty))
        # Deny opponent: prefer moves that also increase opponent distance to target
        opp_d = dist((ox, oy), (tx, ty))
        # Penalize proximity to opponent to avoid giving easy captures
        opp_close = dist((nx, ny), (ox, oy))
        # Small bias to reduce distance to opponent if we are behind (score shaping based on distances to target)
        if best_t is not None:
            my_curr = dist((sx, sy), (tx, ty))
            behind = 1 if my_curr > opp_d else 0
        else:
            behind = 0
        score = my_d - 0.15 * (opp_close) + (0.08 * behind * my_d)
        # Extra heuristic: if target is present, go around obstacles by preferring moves that don't reduce clearance
        if resources:
            # count adjacent obstacle cells as local "risk"
            risk = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx + ax, ny + ay
                    if inb(px, py) and (px, py) in obstacles:
                        risk += 1
            score += 0.35 * risk

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer moves that are more direct to target
            if dist((sx + dx, sy + dy), (tx, ty)) < dist((sx + best_move[0], sy + best_move[1]), (tx, ty)):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]